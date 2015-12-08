
import { CALL_API } from 'middleware/api'
import { make_url } from 'utils'

export const LIST_REQUEST = 'LIST_REQUEST'
export const LIST_SUCCESS = 'LIST_SUCCESS'
export const LIST_FAILURE = 'LIST_FAILURE'

function fetchList (page = 1, sublist = 'latest') {
  return {
    [CALL_API]: {
      types: [LIST_REQUEST, LIST_SUCCESS, LIST_FAILURE],
      endpoint: make_url.list(sublist) + '?page=' + page,
      key: 'list'
    }
  }
}

export function loadList (page = 1, sublist = 'latest') {
  return (dispatch, getState) => {
    return dispatch(fetchList(page = page, sublist = sublist))
  }
}
