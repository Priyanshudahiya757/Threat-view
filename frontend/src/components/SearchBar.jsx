import { useState } from 'react'
import PropTypes from 'prop-types'
import { FiSearch } from 'react-icons/fi'

function SearchBar({ onSearch, placeholder = 'Search...', initialValue = '' }) {
  const [term, setTerm] = useState(initialValue)

  const handleSubmit = (event) => {
    event.preventDefault()
    onSearch(term)
  }

  return (
    <form className="search-bar" onSubmit={handleSubmit} role="search">
      <FiSearch className="search-bar__icon" size={16} />
      <input
        type="text"
        className="search-bar__input"
        placeholder={placeholder}
        value={term}
        onChange={(event) => setTerm(event.target.value)}
        aria-label="Search indicator"
      />
      <button type="submit" className="btn btn-primary search-bar__button">
        Search
      </button>
    </form>
  )
}

SearchBar.propTypes = {
  onSearch: PropTypes.func.isRequired,
  placeholder: PropTypes.string,
  initialValue: PropTypes.string,
}

export default SearchBar
