import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { getStoreEntity } from 'utils'
import { Link } from 'react-router'

class TopicView extends Component {

  static propTypes = {
    dispatch: PropTypes.func,
    topic: PropTypes.shape({
      type: PropTypes.string.isRequired,
      title: PropTypes.string.isRequired,
      text: PropTypes.string,
      comments_count: PropTypes.number,
      created_at: PropTypes.string.isRequired,
      id: PropTypes.number.isRequired,
      link: PropTypes.shape({
        image_url: PropTypes.string,
        description: PropTypes.string,
        title: PropTypes.string,
        url: PropTypes.string
      })
    })
  }

  render () {
    const { topic } = this.props
    let linkEmbed = null
    let textEmbed = null

    if (topic.link){
      linkEmbed = <a href={topic.link.url}>
                    <div>
                      <img src={topic.link.image_url} />
                      <h3>{topic.link.title}</h3>
                      <p>{topic.link.description}</p>
                    </div>
                  </a>;
    }

    if (topic.text){
      textEmbed = <p>{topic.text}</p>
    }

    return <div>
            <span>{topic.created_at}</span>
            <h2><a href={topic.url} target='_blank'>{topic.title}</a></h2>
            {linkEmbed}
            {textEmbed}
          </div>
  }
}

function mapStateToProps (state, ownProps) {
  const { topicId } = ownProps.params
  const topic = getStoreEntity(state, {id: topicId, type: 'topic'})

  return { topic }
}

export default connect(
  mapStateToProps
)(TopicView)
