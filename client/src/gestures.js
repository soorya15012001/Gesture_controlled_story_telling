export function zoomIn(element) {
  const wheelEvt = document.createEvent('MouseEvents');
  wheelEvt.initEvent('wheel', true, true);

// Set deltaY depending on wheel up or wheel down
  wheelEvt.deltaY = -50;
// wheelEvt.deltaY = -120;

// Pass event to element
  element.dispatchEvent(wheelEvt);
}

export function zoomOut(element) {
  const wheelEvt = document.createEvent('MouseEvents');
  wheelEvt.initEvent('wheel', true, true);

// Set deltaY depending on wheel up or wheel down
  wheelEvt.deltaY = 50;
// wheelEvt.deltaY = -120;

// Pass event to element
  element.dispatchEvent(wheelEvt);
}