import * as THREE from 'three'
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js'
import * as dat from 'lil-gui'
import Stats from 'three/examples/jsm/libs/stats.module'

import { CollisionGeometry } from './CollisionGeometry';

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

/**
 * Geometry
 */

// let count = 0;
// let data = [];

// fetch('data/every1000-selected/canup.0221.speck')
//     .then(resp => resp.text())
//     .then(data => {
//         data = data.split("\n").slice(3,-1)
//         count = data.length;

//         const geometry = new THREE.BufferGeometry()

//         const positions = new Float32Array(count * 3)

//         for(let i = 0; i < count; i++)
//         {
//             const [x, z, y, d] = data[i].split(" ")

//             const i3 = i * 3
//             positions[i3    ] = x
//             positions[i3 + 1] = y
//             positions[i3 + 2] = z
//         }

//         geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3))

//         const material = new THREE.PointsMaterial({
//             size: 0.1,
//             sizeAttenuation: true,
//             depthWrite: false,
//             blending: THREE.AdditiveBlending
//         })

//         const points = new THREE.Points(geometry, material)
//         scene.add(points)
//     })

const collision = await new CollisionGeometry()
scene.add(collision.points)

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
 * Animate
 */
const clock = new THREE.Clock()

const tick = async () =>
{
    const elapsedTime = clock.getElapsedTime()

    // Update controls
    controls.update()

    // Next frame
    // await collision.loadPositions()

    // Render
    renderer.render(scene, camera)

    // Call tick again on the next frame
    window.requestAnimationFrame(tick)

    stats.update()
}

tick()