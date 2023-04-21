import * as THREE from 'three'

export class CollisionGeometry {
    constructor() {
        return this.init();
    }

    async init() {
        this.step = 0;
        this.geometry = new THREE.BufferGeometry()
        this.material = new THREE.PointsMaterial({
            size: 0.1,
            sizeAttenuation: true,
            depthWrite: false,
            blending: THREE.AdditiveBlending
        })
        this.count = 1172
        this.positions = []
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
        this.frames = 3525
        this.loadPositions()
        return this
    }

    loadPositions() {
        fetch(`http://localhost:3000/data/1`)
            .then(resp => resp.json())
            .then(data => {
                for (let i=0; i<data.position.length; i++) {
                    const [x, z, y, d] = data.position[i]

                    const i3 = i * 3
                    this.position[i3    ] = x
                    this.position[i3 + 1] = y
                    this.position[i3 + 2] = z
                }
                this.geometry.attributes.position.needsUpdate = true
                this.step += 1
                fetch(`http://localhost:3000/data/`)
                  .then(resp => resp.json())
                  .then(data => {
                      this.positions = data.position
                  })
            })

    }

    next() {
        for (let i=0; i<this.count; i++) {
            const [x, z, y, d] = this.positions[this.step][i]

            const i3 = i * 3
            this.position[i3    ] = x
            this.position[i3 + 1] = y
            this.position[i3 + 2] = z
        }
        this.geometry.attributes.position.needsUpdate = true
        this.step += 1
        if (this.step === this.frames) this.step = 0
    }

    // next() {
    //     return fetch(`http://localhost:3000/data/${this.step}`)
    //       .then(resp => resp.json())
    //       .then(data => {
    //         for(let i = 0; i < data.position.length; i++)
    //           {
    //             const [x, z, y, d] = data.position[i]
    //
    //             const i3 = i * 3
    //             this.position[i3    ] = x
    //             this.position[i3 + 1] = y
    //             this.position[i3 + 2] = z
    //           }
    //           this.geometry.attributes.position.needsUpdate = true
    //           this.step += 1
    //           if (this.step === this.frames) this.step = 1
    //       })
    // }

    filename = () =>
        `data/every1000-selected-1-30/canup.${this.step.toString().padStart(4,'0')}.speck`

}
