import React from 'react'
import { addExtension, addNamedExtension } from 'config/extensions'
import { Route } from 'react-router'
import { STORY_SUBMIT, STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE } from './consts'

import simpleSubmit from 'reducers/simple_submit'

// import SubmitView from './views/SubmitView'
import VideoView from './views/VideoView'
// import TopicView from './views/LinkView';

addNamedExtension('reducers', STORY_SUBMIT, simpleSubmit({
  types: [ STORY_SUBMIT_REQUEST, STORY_SUBMIT_SUCCESS, STORY_SUBMIT_FAILURE ]
}))

export function setupViews (Application) {
  addExtension('routes',
            <Route key='video' name='video' path='/v/:videoId/(:slug)' component={VideoView} />)
}
