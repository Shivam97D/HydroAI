import React, { useState } from 'react'
import styles from './Loaders.module.css'

export function Loader1() { return <div className={styles.loader1} /> }
export function Loader2() { return <div className={styles.loader2} /> }
export function Loader3() { return <div className={styles.loader3} /> }
export function Loader4() { return <div className={styles.loader4} /> }
export function Loader5() { return <div className={styles.loader5} /> }

const ALL_LOADERS = [Loader1, Loader2, Loader3, Loader4, Loader5]

/**
 * Picks a random loader on each mount — different every time loading appears.
 * For full-size loading areas (dashboard, map, history).
 */
export function RandomLoader() {
  const [L] = useState(() => ALL_LOADERS[Math.floor(Math.random() * ALL_LOADERS.length)])
  return <L />
}

/**
 * Same random selection but scaled to fit inside a button.
 * Uses negative margins to compensate for the scale so the button keeps its shape.
 */
export function RandomLoaderSmall() {
  // [scale, horizontal margin compensation, vertical margin compensation]
  // native sizes: L1=50x50, L2=40x80, L3=80x40, L4=80x40, L5=60x60
  const CONFIGS: [number, number, number][] = [
    [0.40, -15, -15],   // L1 50x50  → ~20x20
    [0.32, -14, -27],   // L2 40x80  → ~13x26
    [0.55, -18,  -9],   // L3 80x40  → ~44x22
    [0.55, -18,  -9],   // L4 80x40  → ~44x22
    [0.38, -19, -19],   // L5 60x60  → ~23x23
  ]
  const [idx] = useState(() => Math.floor(Math.random() * ALL_LOADERS.length))
  const L = ALL_LOADERS[idx]
  const [scale, mh, mv] = CONFIGS[idx]

  return (
    <span style={{
      display: 'inline-block',
      transform: `scale(${scale})`,
      transformOrigin: 'center',
      margin: `${mv}px ${mh}px`,
      flexShrink: 0,
    }}>
      <L />
    </span>
  )
}
