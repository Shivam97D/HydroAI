import React, { useState, useEffect, useRef } from 'react'
import SubscribeWidget from '../components/SubscribeWidget'
import styles from './AwarenessPage.module.css'

export default function AwarenessPage() {
  const [scrollY, setScrollY] = useState(0)

  useEffect(() => {
    const h = () => setScrollY(window.scrollY)
    window.addEventListener('scroll', h, { passive: true })
    return () => window.removeEventListener('scroll', h)
  }, [])

  return (
    <div className={styles.page}>
      <section className={styles.hero}>
        <div className={styles.heroBg} style={{ transform: `translateY(${scrollY * 0.4}px)` }} />
        <div className={styles.heroOverlay} />
        <div className={styles.heroContent}>
          <span className={styles.heroTag}>Flood Awareness</span>
          <h1 className={styles.heroTitle}>Stay Informed.<br />Stay Safe.</h1>
          <p className={styles.heroDesc}>
            Understanding floods is the first step to surviving them. Learn how to prepare,
            respond, and recover — and subscribe to get real-time alerts before the water rises.
          </p>
        </div>
      </section>

      <div className={styles.sections}>
        <FadeSection>
          <WhatIsFlood />
        </FadeSection>
        <FadeSection>
          <BeforeFlood />
        </FadeSection>
        <FadeSection>
          <DuringFlood />
        </FadeSection>
        <FadeSection>
          <AfterFlood />
        </FadeSection>
        <FadeSection>
          <EmergencyContacts />
        </FadeSection>
        <FadeSection>
          <SubscribeCTA />
        </FadeSection>
      </div>
    </div>
  )
}

function FadeSection({ children }: { children: React.ReactNode }) {
  const ref = useRef<HTMLDivElement>(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const obs = new IntersectionObserver(
      ([e]) => { if (e.isIntersecting) setVisible(true) },
      { threshold: 0.1 }
    )
    if (ref.current) obs.observe(ref.current)
    return () => obs.disconnect()
  }, [])

  return (
    <div ref={ref} className={`${styles.fadeSection} ${visible ? styles.visible : ''}`}>
      {children}
    </div>
  )
}

function WhatIsFlood() {
  const types = [
    { icon: '⚡', title: 'Flash Floods', desc: 'Rapid floods caused by intense rainfall over a short period. Can occur within minutes or hours of heavy precipitation.' },
    { icon: '🌊', title: 'River Floods', desc: 'Occur when rivers overflow their banks due to sustained heavy rainfall or snowmelt. Can last days to weeks.' },
    { icon: '🌀', title: 'Coastal Floods', desc: 'Caused by storm surges, cyclones, and high tides. Saltwater intrusion damages crops, infrastructure, and drinking water.' },
    { icon: '🏙️', title: 'Urban Floods', desc: 'Stormwater overwhelms drainage systems in cities. Impervious surfaces increase runoff and flood severity significantly.' },
  ]

  return (
    <section>
      <h2 className={styles.sectionTitle}>Understanding Floods</h2>
      <p className={styles.sectionSubtitle}>India experiences multiple types of floods annually, affecting millions across states like Maharashtra, Kerala, Bihar, and Assam.</p>
      <div className={styles.cardGrid}>
        {types.map(t => (
          <div key={t.title} className={styles.infoCard}>
            <div className={styles.cardIcon}>{t.icon}</div>
            <h3 className={styles.cardTitle}>{t.title}</h3>
            <p className={styles.cardDesc}>{t.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function BeforeFlood() {
  const items = [
    { icon: '🎒', text: 'Prepare an emergency kit: water (3L/person/day), food for 3 days, first aid, torch, batteries, whistle, and important documents.' },
    { icon: '🗺️', text: 'Know your evacuation routes. Identify two routes from home, and designate a meeting point for your family.' },
    { icon: '📄', text: 'Waterproof all critical documents: Aadhaar, land records, insurance papers, bank documents, and medical records in a sealed bag.' },
    { icon: '📱', text: 'Download the Sachet or NDMA app for government flood alerts. Save emergency numbers in your phone.' },
    { icon: '🏠', text: 'Elevate electrical appliances and valuables above potential flood levels. Know how to turn off electricity and gas.' },
    { icon: '🤝', text: 'Know your neighbours — especially elderly or disabled residents who may need extra help during evacuation.' },
  ]

  return (
    <section>
      <h2 className={styles.sectionTitle}>Before a Flood</h2>
      <p className={styles.sectionSubtitle}>Preparation can mean the difference between life and death. Do these now, before a flood warning is issued.</p>
      <div className={styles.checklist}>
        {items.map((item, i) => (
          <div key={i} className={styles.checkItem}>
            <span className={styles.checkIcon}>{item.icon}</span>
            <span>{item.text}</span>
          </div>
        ))}
      </div>
    </section>
  )
}

function DuringFlood() {
  const dos = [
    'Move immediately to higher ground — do not wait for instructions.',
    'Listen to All India Radio, local authorities, and official social media for updates.',
    'Turn off electricity at the main switch if water is entering your home.',
    'Take your emergency kit and important documents before evacuating.',
    'Help neighbours — especially the elderly, children, and people with disabilities.',
    'If caught in flowing water, grab onto something stable and call for help.',
  ]

  const donts = [
    'Do NOT walk, swim, or drive through floodwater — even 15 cm can knock you down.',
    'Do NOT touch electrical equipment or downed power lines in flooded areas.',
    'Do NOT return home until authorities declare it safe.',
    'Do NOT use gas appliances until they have been checked for safety.',
    'Do NOT ignore evacuation orders — flash floods can develop in minutes.',
    'Do NOT drink floodwater — it is contaminated with sewage, chemicals, and pathogens.',
  ]

  return (
    <section>
      <h2 className={styles.sectionTitle}>During a Flood</h2>
      <p className={styles.sectionSubtitle}>Act fast and stay calm. Your actions in the first hour are critical.</p>
      <div className={styles.dosDonts}>
        <div>
          <h3 className={styles.listHeading} style={{ color: '#16A34A' }}>✓ Do</h3>
          <div className={styles.doList}>
            {dos.map((d, i) => (
              <div key={i} className={styles.doItem}>
                <span className={styles.doIcon}>✓</span>
                <span>{d}</span>
              </div>
            ))}
          </div>
        </div>
        <div>
          <h3 className={styles.listHeading} style={{ color: '#DC2626' }}>✕ Don't</h3>
          <div className={styles.dontList}>
            {donts.map((d, i) => (
              <div key={i} className={styles.dontItem}>
                <span className={styles.dontIcon}>✕</span>
                <span>{d}</span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  )
}

function AfterFlood() {
  const steps = [
    { icon: '🔍', title: 'Wait for clearance', desc: 'Do not return home until local authorities say it is safe. Floodwater may still be rising or the structure may be unsafe.' },
    { icon: '⚠️', title: 'Beware of contamination', desc: 'Floodwater carries sewage, chemicals, and disease. Wear rubber boots and gloves. Boil all drinking water until declared safe.' },
    { icon: '📸', title: 'Document damage', desc: 'Before cleaning up, photograph all damage for insurance claims. Contact your insurer immediately and keep all repair receipts.' },
    { icon: '🦟', title: 'Prevent disease', desc: 'Drain standing water to prevent mosquito breeding. Clean and disinfect all surfaces, furniture, and appliances that got wet.' },
    { icon: '🏗️', title: 'Structural checks', desc: 'Have a professional check foundations, walls, and electrical systems before occupying the building. Watch for cracks and sagging.' },
    { icon: '💚', title: 'Mental health', desc: 'Floods are traumatic. Talk to family, community workers, or counsellors. NIMHANS helpline: 080-46110007.' },
  ]

  return (
    <section>
      <h2 className={styles.sectionTitle}>After a Flood</h2>
      <p className={styles.sectionSubtitle}>Recovery is a process. Take it step by step — your safety comes first, always.</p>
      <div className={styles.cardGrid}>
        {steps.map(s => (
          <div key={s.title} className={styles.infoCard}>
            <div className={styles.cardIcon}>{s.icon}</div>
            <h3 className={styles.cardTitle}>{s.title}</h3>
            <p className={styles.cardDesc}>{s.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}

function EmergencyContacts() {
  const contacts = [
    { org: 'National Disaster Management Authority', number: '1078', type: 'National' },
    { org: 'National Emergency', number: '112', type: 'National' },
    { org: 'Ambulance', number: '108', type: 'National' },
    { org: 'Fire & Rescue', number: '101', type: 'National' },
    { org: 'Police', number: '100', type: 'National' },
    { org: 'NDRF (National Disaster Response Force)', number: '011-24363260', type: 'National' },
    { org: 'IMD Weather Helpline', number: '1800-180-1717', type: 'National' },
    { org: 'Maharashtra Disaster Management Cell', number: '1077', type: 'State' },
    { org: 'Kerala State Disaster Mgmt. Authority', number: '0471-2364424', type: 'State' },
    { org: 'Assam Disaster Management Authority', number: '0361-2237219', type: 'State' },
  ]

  return (
    <section>
      <h2 className={styles.sectionTitle}>Emergency Contacts</h2>
      <p className={styles.sectionSubtitle}>Save these numbers now. During a flood, networks get congested — know them by heart.</p>
      <div className={styles.tableWrap}>
        <table className={styles.emergencyTable}>
          <thead>
            <tr>
              <th>Organisation</th>
              <th>Number</th>
              <th>Scope</th>
            </tr>
          </thead>
          <tbody>
            {contacts.map(c => (
              <tr key={c.number}>
                <td>{c.org}</td>
                <td><span className={styles.emergencyNumber}>{c.number}</span></td>
                <td><span className={`${styles.scopeBadge} ${c.type === 'National' ? styles.national : styles.state}`}>{c.type}</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  )
}

function SubscribeCTA() {
  return (
    <div className={styles.subscribeCTA}>
      <div className={styles.ctaInner}>
        <span className={styles.ctaBell}>🔔</span>
        <h2 className={styles.ctaTitle}>Get Flood Alerts Before It's Too Late</h2>
        <p className={styles.ctaDesc}>
          Subscribe to HydroAI alerts — we'll notify you when high flood risk is detected in your region,
          powered by real-time ERA5 rainfall and GloFAS river discharge data.
        </p>
        <SubscribeWidget dark />
      </div>
    </div>
  )
}
