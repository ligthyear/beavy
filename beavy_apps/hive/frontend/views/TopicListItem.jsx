import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { make_url, getStoreEntity } from 'utils'
import { Link } from 'react-router'

class TopicListItem extends Component {

  static propTypes = {
    entry: PropTypes.shape({
      type: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      url: PropTypes.string.isRequired,
      created_at: PropTypes.string.isRequired,
      id: PropTypes.number.isRequired
    })
  }

  render () {
    return <Link to={make_url.object(this.props.entry.id)}>
          <div>
            <span>{this.props.entry.created_at}</span>
            <h2>{this.props.entry.title || this.props.entry.title}</h2>
          </div>
        </Link>
  }
}

export default connect(
  function (state, ownProps) {
    const entry = getStoreEntity(state, ownProps.entry)
    return {entry: entry}
  }
)(TopicListItem)
