import PropTypes from 'prop-types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const TOOLTIP_STYLE = { background: '#131a30', border: '1px solid #232b4d', borderRadius: 8, fontSize: 13 }
const TOOLTIP_ITEM_STYLE = { color: '#e9ecf7' }
const TOOLTIP_LABEL_STYLE = { color: '#8891b3' }

function CategoryBarChart({ data }) {
  const chartData = (data || []).map((item) => ({ name: item.name, count: item.count }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData} layout="vertical" margin={{ left: 24 }}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232b4d" horizontal={false} />
        <XAxis type="number" stroke="#8891b3" allowDecimals={false} tick={{ fontSize: 11 }} />
        <YAxis type="category" dataKey="name" stroke="#8891b3" width={120} tick={{ fontSize: 12 }} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          itemStyle={TOOLTIP_ITEM_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          cursor={{ fill: 'rgba(139, 108, 246, 0.08)' }}
        />
        <Bar dataKey="count" fill="#8b6cf6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

CategoryBarChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({ name: PropTypes.string, count: PropTypes.number })),
}

export default CategoryBarChart
