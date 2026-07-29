import PropTypes from 'prop-types'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'

const TOOLTIP_STYLE = { background: '#131a30', border: '1px solid #232b4d', borderRadius: 8, fontSize: 13 }
const TOOLTIP_ITEM_STYLE = { color: '#e9ecf7' }
const TOOLTIP_LABEL_STYLE = { color: '#8891b3' }

function CountryDistributionChart({ data }) {
  const chartData = (data || []).map((item) => ({ name: item.name, count: item.count }))

  return (
    <ResponsiveContainer width="100%" height={260}>
      <BarChart data={chartData}>
        <CartesianGrid strokeDasharray="3 3" stroke="#232b4d" vertical={false} />
        <XAxis
          dataKey="name"
          stroke="#8891b3"
          tick={{ fontSize: 11 }}
          interval={0}
          angle={-25}
          textAnchor="end"
          height={60}
        />
        <YAxis stroke="#8891b3" allowDecimals={false} tick={{ fontSize: 11 }} />
        <Tooltip
          contentStyle={TOOLTIP_STYLE}
          itemStyle={TOOLTIP_ITEM_STYLE}
          labelStyle={TOOLTIP_LABEL_STYLE}
          cursor={{ fill: 'rgba(76, 111, 255, 0.08)' }}
        />
        <Bar dataKey="count" fill="#4c6fff" radius={[4, 4, 0, 0]} />
      </BarChart>
    </ResponsiveContainer>
  )
}

CountryDistributionChart.propTypes = {
  data: PropTypes.arrayOf(PropTypes.shape({ name: PropTypes.string, count: PropTypes.number })),
}

export default CountryDistributionChart
