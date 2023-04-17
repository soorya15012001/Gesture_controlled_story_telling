import * as THREE from 'three'

export class CollisionGeometry {
    constructor() {
        return this.init();
    }

    async init() {
        this.step = 1;
        this.geometry = new THREE.BufferGeometry()
        this.material = new THREE.PointsMaterial({
            size: 0.1,
            sizeAttenuation: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        })
        this.count = await fetch(this.filename())
            .then(resp => resp.text())
            .then(data => this.count = data.split("\n").slice(3,-1).length)
        this.position = new Float32Array(this.count*3)
        this.geometry = new THREE.BufferGeometry()
        this.geometry.setAttribute('position', new THREE.BufferAttribute(this.position, 3))
        this.material = new THREE.PointsMaterial({
            size: 0.1,
            sizeAttenuation: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        })
        this.points = new THREE.Points(this.geometry, this.material)
        this.frames = 100
        await this.loadPositions()
        return this
    }

    loadPositions() {
        return fetch(this.filename(this.step))
            .then(resp => resp.text())
            .then(data => {
                data = data.split("\n").slice(3,-1)
                for(let i = 0; i < this.count; i++)
                {
                    const [x, z, y, d] = data[i].split(" ")
        
                    const i3 = i * 3
                    this.position[i3    ] = x
                    this.position[i3 + 1] = y
                    this.position[i3 + 2] = z
                }
                this.geometry.attributes.position.needsUpdate = true
                this.step += 1
                if (this.step === this.frames) this.step = 1
            })
        
    }

    filename = () =>
        `data/every1000/canup.${this.step.toString().padStart(4,'0')}.speck`
    
}
