import { useEffect } from 'react'
import PropTypes from 'prop-types'
import { FiX } from 'react-icons/fi'

function Modal({ title, isOpen, onClose, children }) {
  useEffect(() => {
    if (!isOpen) return undefined
    const handleKeyDown = (event) => {
      if (event.key === 'Escape') onClose()
    }
    document.addEventListener('keydown', handleKeyDown)
    return () => document.removeEventListener('keydown', handleKeyDown)
  }, [isOpen, onClose])

  if (!isOpen) return null

  return (
    <div className="tv-modal-backdrop" onClick={onClose}>
      {/* eslint-disable-next-line jsx-a11y/no-noninteractive-element-interactions */}
      <div className="tv-modal" role="dialog" aria-modal="true" onClick={(event) => event.stopPropagation()}>
        <div className="tv-modal__header">
          <h5 className="tv-modal__title">{title}</h5>
          <button type="button" className="tv-modal__close" onClick={onClose} aria-label="Close">
            <FiX size={18} />
          </button>
        </div>
        <div className="tv-modal__body">{children}</div>
      </div>
    </div>
  )
}

Modal.propTypes = {
  title: PropTypes.string,
  isOpen: PropTypes.bool.isRequired,
  onClose: PropTypes.func.isRequired,
  children: PropTypes.node,
}

export default Modal
