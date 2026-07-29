import PropTypes from 'prop-types'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const TOOLTIP_STYLE = { background: '#131a30', border: '1px solid #232b4d', borderRadius: 8, fontSize: 13 }
const TOOLTIP_ITEM_STYLE = { color: '#e9ecf7' }
const TOOLTIP_LABEL_STYLE = { color: '#8891b3' }

function ThreatTrendChart({ data }) {
  return (
    <ResponsiveContainer width="100%" height={260}>
      <LineChart data={data || []}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232b4d" vertical={false} />
        <XAxis dataKey="date" stroke="#8891b3" tick={{ fontSize: 11 }} />
        <YAxis stroke="#8891b3" allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip contentStyle={TOOLTIP_STYLE} itemStyle={TOOLTIP_ITEM_STYLE} labelStyle={TOOLTIP_LABEL_STYLE} />
        <Line type="monotone" dataKey="count" stroke="#f4415c" strokeWidth={2} dot={false} activeDot={{ r: 4 }} />
      </LineChart>
    </ResponsiveContainer>
  )
}

ThreatTrendChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({ date: PropTypes.string, count: PropTypes.number })),
}

export default ThreatTrendChart
