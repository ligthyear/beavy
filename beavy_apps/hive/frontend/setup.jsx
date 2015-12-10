import React from 'react'
import { addExtension, addNamedExtension } from 'config/extensions'
import { Route } from 'react-router'
import { STORY_SUBMIT, STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE } from './consts'

import simpleSubmit from 'reducers/simple_submit'

import SubmitView from './views/SubmitView'
import TopicView from './views/TopicView'
import TopicListItem from './views/TopicListItem'
// import TopicView from './views/TopicView';

addNamedExtension('reducers', STORY_SUBMIT, simpleSubmit({
  types: [ STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE ]
}))

export function setupViews (Application) {
  addNamedExtension('listItemRenderer', 'topic', TopicListItem)

  addExtension('routes',
      <Route key='submit' name='submit' path='/submit/' component={SubmitView} />)

  addExtension('routes',
            <Route key='link' name='link' path='/t/:linkId/(:slug)' component={TopicView} />)
}
