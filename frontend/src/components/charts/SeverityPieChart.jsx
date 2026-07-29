import PropTypes from 'prop-types'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const COLORS = {
  critical: '#e11d48',
  high: '#f4415c',
  medium: '#f5a623',
  low: '#4c6fff',
}
const FALLBACK_COLOR = '#8891b3'
const TOOLTIP_STYLE = { background: '#131a30', border: '1px solid #232b4d', borderRadius: 8, fontSize: 13 }
const TOOLTIP_ITEM_STYLE = { color: '#e9ecf7' }
const TOOLTIP_LABEL_STYLE = { color: '#8891b3' }
const LEGEND_STYLE = { fontSize: 12, color: '#8891b3' }

function SeverityPieChart({ data }) {
  const chartData = Object.entries(data || {}).map(([severity, count]) => ({
    name: severity.charAt(0).toUpperCase() + severity.slice(1),
    key: severity,
    value: count,
  }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" innerRadius={60} outerRadius={90} paddingAngle={3}>
          {chartData.map((entry) => (
            <Cell key={entry.key} fill={COLORS[entry.key] || FALLBACK_COLOR} />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} itemStyle={TOOLTIP_ITEM_STYLE} labelStyle={TOOLTIP_LABEL_STYLE} />
        <Legend wrapperStyle={LEGEND_STYLE} />
      </PieChart>
    </ResponsiveContainer>
  )
}

SeverityPieChart.propTypes = {
  data: PropTypes.objectOf(PropTypes.number),
}

export default SeverityPieChart
