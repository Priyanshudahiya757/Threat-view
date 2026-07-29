import PropTypes from 'prop-types'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts'

const TOOLTIP_STYLE = {
  background: 'var(--color-bg-card, #0f172a)',
  border: '1px solid var(--color-border, #1e293b)',
  borderRadius: '8px',
  boxShadow: '0 10px 25px -5px rgba(0,0,0,0.5)',
  fontSize: '13px',
  padding: '10px 14px',
}

const CustomTooltip = ({ active, payload }) => {
  if (!active || !payload || !payload.length) return null
  const data = payload[0].payload
  const bucket = data.bucket
  const count = data.count
  const scoreVal = parseInt(bucket.split('-')[0], 10)

  let risk = 'Normal / Low Risk'
  let color = 'var(--color-accent, #3b82f6)'
  if (scoreVal >= 70) {
    risk = 'Critical Anomaly Risk'
    color = 'var(--color-critical, #f4415c)'
  } else if (scoreVal >= 40) {
    risk = 'Elevated Risk'
    color = 'var(--color-high, #f97316)'
  }

  return (
    <div style={TOOLTIP_STYLE}>
      <div style={{ fontWeight: 600, color: 'var(--color-text, #f8fafc)', marginBottom: '4px' }}>
        Score Range: {bucket}
      </div>
      <div style={{ color: '#94a3b8', fontSize: '12px', marginBottom: '6px' }}>
        Indicators in Bucket: <strong style={{ color: '#f8fafc' }}>{count}</strong>
      </div>
      <div style={{ color, fontSize: '12px', fontWeight: 600, display: 'flex', alignItems: 'center', gap: '6px' }}>
        <span style={{ width: 8, height: 8, borderRadius: '50%', backgroundColor: color, display: 'inline-block' }} />
        {risk}
      </div>
    </div>
  )
}

CustomTooltip.propTypes = {
  active: PropTypes.bool,
  payload: PropTypes.array,
}

function AnomalyDistributionChart({ data }) {
  const chartData = (data || []).map((item) => ({
    bucket: item.bucket,
    count: item.count,
  }))

  return (
    <div style={{ width: '100%', height: 260, minWidth: 0 }}>
      <ResponsiveContainer width="100%" height="100%">
        <BarChart data={chartData} margin={{ top: 15, right: 20, left: -10, bottom: 25 }}>
          <defs>
            <linearGradient id="gradNormal" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#4c6fff" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#4c6fff" stopOpacity={0.4} />
            </linearGradient>
            <linearGradient id="gradHigh" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f5a623" stopOpacity={0.9} />
              <stop offset="100%" stopColor="#f5a623" stopOpacity={0.4} />
            </linearGradient>
            <linearGradient id="gradCritical" x1="0" y1="0" x2="0" y2="1">
              <stop offset="0%" stopColor="#f4415c" stopOpacity={0.95} />
              <stop offset="100%" stopColor="#f4415c" stopOpacity={0.4} />
            </linearGradient>
          </defs>

          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255, 255, 255, 0.07)" vertical={false} />
          
          <XAxis
            dataKey="bucket"
            stroke="#64748b"
            tick={{ fontSize: 11, fill: '#94a3b8' }}
            label={{ value: 'Anomaly Score Bucket (0-100)', position: 'insideBottom', offset: -15, fill: '#64748b', fontSize: 12 }}
          />
          <YAxis
            stroke="#64748b"
            allowDecimals={false}
            tick={{ fontSize: 11, fill: '#94a3b8' }}
            label={{ value: 'Indicator Count', angle: -90, position: 'insideLeft', offset: 15, fill: '#64748b', fontSize: 12 }}
          />

          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255, 255, 255, 0.03)' }} />

          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {chartData.map((entry, index) => {
              const scoreVal = index * 10
              let fill = 'url(#gradNormal)'
              if (scoreVal >= 70) fill = 'url(#gradCritical)'
              else if (scoreVal >= 40) fill = 'url(#gradHigh)'

              return <Cell key={`bar-cell-${index}`} fill={fill} />
            })}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

AnomalyDistributionChart.propTypes = {
  data: PropTypes.arrayOf(
    PropTypes.shape({
      bucket: PropTypes.string,
      count: PropTypes.number,
    })
  ),
}

export default AnomalyDistributionChart
