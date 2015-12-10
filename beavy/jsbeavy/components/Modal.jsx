import React from 'react'
import styles from './Modal.scss'
import classnames from 'classnames'

export class Modal extends React.Component {
  propTypes: {
    onRequestClose: React.PropTypes.func,
    // title: React.PropTypes.string,
    // closeTimeoutMS: React.PropTypes.number,
    ariaHideApp: React.PropTypes.bool
  }

  defaultProps: {
    isOpen: true,
    ariaHideApp: true,
    // closeTimeoutMS: 0
  }
  render () {
    return <div name="modalFrame" className={classnames(styles.modal, styles.open)}>
            <div className={styles.modalFadeScreen}>
              <div className={styles.modalInner}>
                <div onClick={this.props.onRequestClose} className={styles.modalClose}></div>
                {this.props.children}
              </div>
            </div>
          </div>
  }
}
