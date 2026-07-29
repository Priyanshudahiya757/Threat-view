import PropTypes from 'prop-types'
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from 'recharts'

const PALETTE = ['#4c6fff', '#8b6cf6', '#f4415c', '#f5a623', '#2dd4bf']
const TOOLTIP_STYLE = { background: '#131a30', border: '1px solid #232b4d', borderRadius: 8, fontSize: 13 }
const TOOLTIP_ITEM_STYLE = { color: '#e9ecf7' }
const LEGEND_STYLE = { fontSize: 12, color: '#8891b3' }

function TopSourcesChart({ data }) {
  const chartData = (data || []).map((item) => ({ name: item.name, value: item.count }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <PieChart>
        <Pie data={chartData} dataKey="value" nameKey="name" outerRadius={90}>
          {chartData.map((entry, index) => (
            <Cell key={entry.name} fill={PALETTE[index % PALETTE.length]} />
          ))}
        </Pie>
        <Tooltip contentStyle={TOOLTIP_STYLE} itemStyle={TOOLTIP_ITEM_STYLE} />
        <Legend wrapperStyle={LEGEND_STYLE} />
      </PieChart>
    </ResponsiveContainer>
  )
}

TopSourcesChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({ name: PropTypes.string, count: PropTypes.number })),
}

export default TopSourcesChart
