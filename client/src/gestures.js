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

export function rotate(element, event) {
    const evt = new PointerEvent(event.name,{
        clientX: event.x * element.width,
        clientY: event.y * element.height,
        pointerId: 1
    })
    console.log("rotate",event, evt)

    element.dispatchEvent(evt)

}

export function translate(element, event) {
    const evt = new PointerEvent(event.name,{
        clientX: event.x * element.width,
        clientY: event.y * element.height,
        pointerId: 1,
        button: 2,
    })
    console.log("translate",event, evt)

    element.dispatchEvent(evt)
}