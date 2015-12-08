
import { addNamedExtension } from 'config/extensions'
import { LIST_REQUEST, LIST_SUCCESS, LIST_FAILURE } from '../actions/list'

import paginate from 'reducers/paginate'

export const LIST = 'list'

addNamedExtension('reducers', LIST, paginate({
  mapActionToKey: x => LIST,
  types: [ LIST_REQUEST, LIST_SUCCESS, LIST_FAILURE ]
}))
