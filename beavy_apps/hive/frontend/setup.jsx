import React from 'react'
import { addExtension, addNamedExtension } from 'config/extensions'
import { Route } from 'react-router'
import { STORY_SUBMIT, STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE } from './consts'

import simpleSubmit from 'reducers/simple_submit'

import SubmitView from './views/SubmitView'
import LinkView from './views/LinkView'
import LinkListItem from './views/LinkListItem'
// import TopicView from './views/LinkView';

addNamedExtension('reducers', STORY_SUBMIT, simpleSubmit({
  types: [ STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE ]
}))

export function setupViews (Application) {
  addNamedExtension('listItemRenderer', 'link', LinkListItem)

  addExtension('routes',
      <Route key='submit' name='submit' path='/submit/' component={SubmitView} />)

  addExtension('routes',
            <Route key='link' name='link' path='/l/:linkId/(:slug)' component={LinkView} />)
}
