import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import * as dat from 'lil-gui'
import {io} from 'socket.io-client'
import Stats from 'three/examples/jsm/libs/stats.module'

import { CollisionGeometry } from './CollisionGeometry';
import { zoomIn, zoomOut } from "./gestures";

// Playback
const playbackIcon = document.querySelector('#playback')
window.play = false

playbackIcon.onclick = () => {
    play = !play
    playbackIcon.src = play ? "pause.svg" : "play.svg"
}

/**
 * Socket
 */

function connect() {
    const socket = io.connect(location.protocol + '//' + document.domain + ':8000', { transports:["websocket"]} );
    socket.on('connect', function() {
        socket.emit('send_data')
    });
    socket.on('receive_dictionary', function(data) {
        const resp = JSON.parse(data)
        if (resp['zoom'] === "Zoom In") zoomIn(canvas)
        else if (resp['zoom'] === "Zoom Out") zoomOut(canvas)
        else if (resp['play'] !== null && resp['play'] !== window.play) playbackIcon.dispatchEvent(new Event('click'))
    });
    socket.on('output_frame', function(outputFrameJPEG) {
        // Decode the JPEG and set it as the source of the video frame
        var video_stream = document.getElementById('video-stream');
        video_stream.src = 'data:image/jpeg;base64,' + outputFrameJPEG;
    });
}

/**
 * Base
 */
// Debug
const gui = new dat.GUI()
const stats = new Stats()
document.body.appendChild(stats.dom)

// Canvas
const canvas = document.querySelector('canvas.webgl')

// Scene
const scene = new THREE.Scene()

/**
 * Sizes
 */
const sizes = {
    width: window.innerWidth,
    height: window.innerHeight
}

/**
 * Camera
 */
// Base camera
const camera = new THREE.PerspectiveCamera(75, sizes.width / sizes.height, 0.1, 100)
scene.add(camera)

// Axes Helper
const axesHelper = new THREE.AxesHelper( 10 );
scene.add( axesHelper );

/**
 * Control
 */
const parameters = {}
parameters.cameraX = -10
parameters.cameraY = 20
parameters.cameraZ = 30
gui.add(parameters, 'cameraX').min(-50).max(50).step(0.1).onChange(() => camera.position.x = parameters.cameraX)
gui.add(parameters, 'cameraY').min(-50).max(50).step(0.1).onChange(() => camera.position.y = parameters.cameraY)
gui.add(parameters, 'cameraZ').min(-50).max(50).step(0.1).onChange(() => camera.position.z = parameters.cameraZ)
camera.position.x = parameters.cameraX
camera.position.y = parameters.cameraY
camera.position.z = parameters.cameraZ


window.addEventListener('resize', () =>
{
    // Update sizes
    sizes.width = window.innerWidth
    sizes.height = window.innerHeight

    // Update camera
    camera.aspect = sizes.width / sizes.height
    camera.updateProjectionMatrix()

    // Update renderer
    renderer.setSize(sizes.width, sizes.height)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
})



// Controls
const controls = new OrbitControls(camera, canvas)
controls.enableDamping = true

/**
 * Renderer
 */
const renderer = new THREE.WebGLRenderer({
    canvas: canvas,
    alpha: true,
})
renderer.setSize(sizes.width, sizes.height)
renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
renderer.setClearColor( 0x000000, 0.8 ); // the default

/**
 * Geometry
 */

const collision = await new CollisionGeometry(connect)
scene.add(collision.points)

/**
 * Animate
 */
const clock = new THREE.Clock()

const tick = async () =>
{
    const elapsedTime = clock.getElapsedTime()

    // Update controls
    controls.update()

    // Next frame
    if (play)
        await collision.next()

    // Render
    renderer.render(scene, camera)

    // Call tick again on the next frame
    window.requestAnimationFrame(tick)

    stats.update()
}

tick()