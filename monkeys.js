/* Opt-in macaque troupe. Only visible time on the page counts toward arrivals. */
function createMonkeyTroupe({root, toggle, label, reduced, translate}) {
  const MAX_MONKEYS = 10, ARRIVAL_MS = 30000;
  const runners = [];
  let enabled = false, busy = false, frame = 0, lastFrame = 0;
  let visibleMs = 0, visibleSince = document.hidden ? null : performance.now();
  let pointer = {x: innerWidth / 2, y: innerHeight / 2}, lastPointerTime = 0;
  const assets = {
    run: 'assets/monkeys/run.webp', walk: 'assets/monkeys/walk.webp',
    jump: 'assets/monkeys/jump-land.webp', sit: 'assets/monkeys/sit.webp',
    scratch: 'assets/monkeys/look-scratch.webp', static: 'assets/monkeys/sit-static.png'
  };
  // Durations from the supplied WebP frames; one-shot files also encode loop=1.
  const durations = {jump: 990, scratch: 4958};
  const images = new Map();
  function preload(state) {
    if (!images.has(state)) {
      const image = new Image();
      image.src = assets[state];
      images.set(state, image);
    }
    return images.get(state).decode();
  }
  function setAnimation(r, state, now) {
    if (r.state === state) return;
    const sprite = document.createElement('img');
    sprite.className = 'monkey-sprite';
    sprite.alt = '';sprite.draggable = false;
    sprite.src = assets[state];
    r.sprite.replaceWith(sprite);r.sprite = sprite;
    r.state = state;r.stateSince = now;
    r.node.dataset.animation = state;
    if (state === 'sit') r.gestureAt = now + 12000 + r.angle * 650;
  }
  function animate(r, now) {
    if (reduced.matches) {setAnimation(r, 'static', now);return}
    if (r.state === 'jump') {
      if (now - r.stateSince < durations.jump) return;
      setAnimation(r, 'sit', now);return;
    }
    if (r.speed > 12) {
      setAnimation(r, r.speed > (r.state === 'run' ? 85 : 110) ? 'run' : 'walk', now);
    } else if (r.state === 'scratch' && now - r.stateSince < durations.scratch) {
      return;
    } else if (r.state === 'sit' && now >= r.gestureAt) {
      setAnimation(r, 'scratch', now);
    } else {
      setAnimation(r, 'sit', now);
    }
  }

  function activeTime(now = performance.now()) {
    return visibleMs + (visibleSince === null ? 0 : now - visibleSince);
  }
  function updateLabel() {
    toggle.setAttribute('aria-pressed', String(enabled));
    label.textContent = translate(enabled ? 'monkeyOff' : 'monkeyOn');
  }
  function bounds(x, y, size) {
    const top = Math.min(100, Math.max(0, innerHeight - size));
    const bottomSpace = innerWidth <= 700 ? 80 : 12;
    return {
      x: Math.max(4, Math.min(Math.max(4, innerWidth - size - 4), x)),
      y: Math.max(top, Math.min(Math.max(top, innerHeight - size - bottomSpace), y))
    };
  }
  function render(r) {
    r.node.style.transform = `translate3d(${r.x.toFixed(2)}px,${r.y.toFixed(2)}px,0)`;
    animate(r, activeTime());
    r.node.classList.toggle('face-left', r.facing < 0);
    r.node.classList.add('arrived');
  }
  function addRunner() {
    const i = runners.length;
    const node = document.createElement('div');
    node.className = 'monkey-runner';
    const sprite = document.createElement('div');
    sprite.className = 'monkey-sprite';
    node.append(sprite);root.append(node);
    const scale = .88 + ((i * 7) % 5) * .04;
    const size = (innerWidth <= 700 ? 65 : 78) * scale;
    node.style.width = node.style.height = `${size}px`;
    const pos = bounds(i % 2 ? innerWidth - size : 6, pointer.y + 60 + (i % 3) * 12, size);
    const runner = {node, sprite, size, scale, x: pos.x, y: pos.y, vx: 0, vy: 0,
      angle: i * 2.399963, radius: i === 0 ? 0 : 38 + Math.sqrt(i) * 24,
      speed: 0, facing: i % 2 ? -1 : 1, pace: 175 + (i * 17) % 65};
    runners.push(runner);
    setAnimation(runner, reduced.matches ? 'static' : 'jump', activeTime());
    render(runner);
  }
  function syncCount() {
    if (!enabled || document.hidden) return;
    const desired = Math.min(MAX_MONKEYS, 1 + Math.floor(activeTime() / ARRIVAL_MS));
    while (runners.length < desired) addRunner();
    root.dataset.count = String(runners.length);
  }
  function targetFor(r, now) {
    const moving = now - lastPointerTime < 1400;
    const seconds = now / 1000;
    // Slow, continuous variations, never random position jumps.
    const wander = moving && !reduced.matches ? 1 : 0;
    const dx = Math.cos(r.angle) * r.radius + Math.sin(seconds * .8 + r.angle) * 11 * wander;
    const dy = Math.sin(r.angle) * r.radius * .55 + Math.sin(seconds * .6 + r.angle * 2) * 8 * wander;
    return bounds(pointer.x - 95 + dx, pointer.y - 30 + dy, r.size);
  }
  function settleReducedMotion() {
    const now = performance.now();
    runners.forEach(r => {const dest = targetFor(r, now);r.x = dest.x;r.y = dest.y;r.vx = r.vy = r.speed = 0;render(r)});
  }
  function tick(now) {
    frame = 0;
    if (!enabled || document.hidden || reduced.matches) return;
    const dt = Math.min(.04, (now - (lastFrame || now)) / 1000);
    lastFrame = now;
    syncCount();
    for (const r of runners) {
      // Let the arrival land before resuming the existing pursuit physics.
      if (r.state === 'jump') {render(r);continue}
      const goal = targetFor(r, now);
      let dx = goal.x - r.x, dy = goal.y - r.y;
      // Soft separation lets the troop spread out without abrupt collision turns.
      for (const other of runners) {
        if (other === r) continue;
        const sx = r.x + r.size / 2 - other.x - other.size / 2;
        const sy = r.y + r.size / 2 - other.y - other.size / 2;
        const d = Math.hypot(sx, sy), space = (r.size + other.size) * .24;
        if (d > .1 && d < space) {const strength = (space - d) * 2;dx += sx / d * strength;dy += sy / d * strength}
      }
      const distance = Math.hypot(dx, dy);
      const speed = distance < 3 ? 0 : Math.min(r.pace, distance * 3.1);
      const desiredVX = distance > .1 ? dx / distance * speed : 0;
      const desiredVY = distance > .1 ? dy / distance * speed : 0;
      const smoothing = 1 - Math.exp(-6 * dt);
      r.vx += (desiredVX - r.vx) * smoothing;
      r.vy += (desiredVY - r.vy) * smoothing;
      const next = bounds(r.x + r.vx * dt, r.y + r.vy * dt, r.size);
      r.x = next.x;r.y = next.y;r.speed = Math.hypot(r.vx, r.vy);
      if (Math.abs(r.vx) > 18) r.facing = Math.sign(r.vx);
      render(r);
    }
    frame = requestAnimationFrame(tick);
  }
  function restart() {
    cancelAnimationFrame(frame);frame = 0;lastFrame = 0;
    if (!enabled || document.hidden) return;
    syncCount();
    if (reduced.matches) settleReducedMotion();
    else frame = requestAnimationFrame(tick);
  }
  toggle.addEventListener('click', async () => {
    if (busy) return;
    if (!enabled) {
      busy = true;
      try {await Promise.all((reduced.matches ? ['static'] : Object.keys(assets)).map(preload))} catch {busy = false;return}
      busy = false;
      const rect = toggle.getBoundingClientRect();
      pointer = {x: rect.right, y: rect.top + 50};
      lastPointerTime = performance.now();
    }
    enabled = !enabled;root.hidden = !enabled;
    if (!enabled) {runners.length = 0;root.replaceChildren();root.dataset.count = '0'}
    updateLabel();restart();
  });
  function onPointer(e) {
    if (!enabled || e.target.closest?.('#monkey-toggle')) return;
    pointer = {x: e.clientX, y: e.clientY};lastPointerTime = performance.now();
    if (reduced.matches) settleReducedMotion();
  }
  addEventListener('pointermove', onPointer, {passive: true});
  addEventListener('pointerdown', onPointer, {passive: true});
  // Touch browsing can become a native scroll; follow the finger without preventing it.
  addEventListener('touchmove', e => {
    const touch = e.touches[0];
    if (touch) onPointer({clientX: touch.clientX, clientY: touch.clientY, target: e.target});
  }, {passive: true});
  addEventListener('resize', () => {
    for (const r of runners) {
      r.size = (innerWidth <= 700 ? 65 : 78) * r.scale;
      r.node.style.width = r.node.style.height = `${r.size}px`;
      const p = bounds(r.x, r.y, r.size);r.x = p.x;r.y = p.y;render(r);
    }
  });
  document.addEventListener('visibilitychange', () => {
    const now = performance.now();
    if (document.hidden && visibleSince !== null) {visibleMs += now - visibleSince;visibleSince = null}
    else if (!document.hidden && visibleSince === null) visibleSince = now;
    restart();
  });
  reduced.addEventListener('change', restart);
  // Growth also works without an animation loop when reduced motion is requested.
  let growthTimer;
  function scheduleGrowth() {
    clearInterval(growthTimer);
    growthTimer = setInterval(() => {
    if (enabled && !document.hidden) {syncCount();if (reduced.matches) settleReducedMotion()}
    }, 1000);
  }
  scheduleGrowth();
  addEventListener('pagehide', () => {
    if (visibleSince !== null) {visibleMs += performance.now() - visibleSince;visibleSince = null}
    cancelAnimationFrame(frame);frame = 0;clearInterval(growthTimer);
  });
  addEventListener('pageshow', () => {
    if (!document.hidden && visibleSince === null) visibleSince = performance.now();
    scheduleGrowth();restart();
  });
  return {updateLabel};
}
