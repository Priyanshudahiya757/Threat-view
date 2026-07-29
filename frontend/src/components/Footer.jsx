function Footer() {
  return (
    <footer className="tv-footer">
      <span>ThreatView &copy; {new Date().getFullYear()}</span>
      <span>Threat intelligence aggregated from AlienVault OTX, PhishTank &amp; URLhaus</span>
    </footer>
  )
}

export default Footer
