const originalAddEventListener = EventTarget.prototype.addEventListener;

const PASSIVE_EVENTS = new Set([
  "wheel",
  "mousewheel",
  "touchstart",
  "touchmove",
]);

EventTarget.prototype.addEventListener = function (
  type: string,
  listener: EventListenerOrEventListenerObject | null,
  options?: boolean | AddEventListenerOptions
) {
  let opts = options;
  if (PASSIVE_EVENTS.has(type)) {
    if (typeof opts === "boolean") {
      opts = { capture: opts, passive: true };
    } else if (!opts) {
      opts = { passive: true };
    } else if (typeof opts === "object" && opts.passive === undefined) {
      opts = { ...opts, passive: true };
    }
  }
  return originalAddEventListener.call(this, type, listener, opts);
};
