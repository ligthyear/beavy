import React, { Component, PropTypes } from 'react'
import { connect } from 'react-redux'
import { loadList } from '../actions/list'
import { make_url, getStoreEntity } from 'utils'
import { getNamedExtensions } from 'config/extensions'
import { Link } from 'react-router'
import { LIST } from '../reducers/list'
import InfiniteList from 'components/InfiniteList'


class SimpleListItem extends Component {

  static propTypes = {
    entry: PropTypes.shape({
      type: PropTypes.string.isRequired,
      created_at: PropTypes.string.isRequired,
      id: PropTypes.number.isRequired
    })
  }

  render () {
    return <Link to={make_url.object(this.props.entry.id)}>
          <div>
            <span>{this.props.entry.created_at}</span>
            <h2>Object: {this.props.entry.id}</h2>
            <pre>{JSON.stringify(this.props.entry, null, ' ')}</pre>
          </div>
          </Link>
  }
}

const FallbackListItem = connect(
  function (state, ownProps) {
    const entry = getStoreEntity(state, ownProps.entry)
    return {entry: entry}
  }
)(SimpleListItem)

function checkObjects (props) {
  const {list} = props
  if (list && list.meta) return true
  props.dispatch(loadList())
}

class ListView extends Component {

  static propTypes = {
    dispatch: PropTypes.func,
    list: PropTypes.object
  }

  componentWillMount () {
    checkObjects(this.props)
  }

  componentWillReceiveProps (nextProps) {
    checkObjects(nextProps)
  }

  loadMore () {
    this.props.dispatch(loadList(this.props.list.meta.next_num))
  }

  getObjectListItemRenderer (x) {
    const Renderer = getNamedExtensions("listItemRenderer")[x.type] || FallbackListItem;
    return <Renderer key={x.type + "_" + x.id} entry={x} />
  }

  render () {
    const { list } = this.props
    if (!list || !list.meta) {
      return <h1><i>Loading list...</i></h1>
    }
    return (
      <div>
        <InfiniteList
          meta={list.meta}
          loader={::this.loadMore}
          minimalItemHeight={24}
          isFetching={list.isFetching}
          >
          {list.data.map(::this.getObjectListItemRenderer)}
        </InfiniteList>
      </div>
    )
  }
}

function mapStateToProps (state, ownProps) {
  let list = state[LIST]
  if (!list || !list.meta) { list = null }

  return { list }
}

export default connect(
  mapStateToProps
)(ListView)
