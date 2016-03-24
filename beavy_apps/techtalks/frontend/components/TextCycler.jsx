/* eslint react/prop-types: 0 */
// Seriously, ESLINT, why the F are you complainng about
// the prop-types in this file?

import React from 'react'
import defaultStyles from 'components/TextCycler.scss'
import classnames from 'classnames'

export const styles = defaultStyles

export class TextTyper extends React.Component {

  static propTypes: {
    onDone: React.PropTypes.func.required,
    word: React.PropTypes.string.required,
    className: React.PropTypes.string,
    undoTimeout: React.PropTypes.Number.required,
    interval: React.PropTypes.Number.required,
  }

  constructor (props) {
    super(props)
    this.state = {slice: 0, letters: '', timer: null}
  }

  render () {
    return <span className={classnames(this.props.className, styles.blinkingCursor)}>{this.state.letters}</span>
  }

  nextLetter () {
    const nextNum = this.state.slice + 1
    if (this.props.word.length >= nextNum) {
      this.setState({letters: this.props.word.slice(0, nextNum),
                     slice: nextNum})
    } else {
      if (this.state.timer) {
        clearInterval(this.state.timer)
      }
      setTimeout(() => this.start(this.undo.bind(this), 100), this.props.undoTimeout)
    }
  }

  undo () {
    const nextNum = this.state.slice - 1
    if (nextNum <= 0) {
      clearInterval(this.state.timer)
      this.props.onDone()
    } else {
      this.setState({letters: this.props.word.slice(0, nextNum),
                      slice: nextNum})
    }
  }

  start (fn, interval) {
    if (this.state.timer) {
      clearInterval(this.state.timer)
    }
    this.setState({timer: setInterval(fn, interval || this.props.interval)})
  }

  componentDidMount () {
    this.start(this.nextLetter.bind(this))
  }

  componentWillUnmount () {
    if (this.state.timer) {
      clearInterval(this.state.timer)
    }
  }

  componentWillReceiveProps (nextProps) {
    this.setState({slice: 0, letters: ''})
    this.start(this.nextLetter.bind(this))
  }
}

export class TextCycler extends React.Component {

  // static propTypes: {
  //   words: React.PropTypes.arrayOf(React.PropTypes.string)
  // }

  constructor (props) {
    super(props)
    this.state = { index: 0 }
  }

  render () {
    const { words } = this.props
    return <TextTyper onDone={this.next_word.bind(this)} word={words[this.state.index]} interval={225} undoTimeout={2000} />
  }

  next_word () {
    const nextNum = this.state.index + 1
    if (nextNum >= this.props.words.length) {
      this.setState({ index: 0 })
    } else {
      this.setState({ index: nextNum })
    }
  }

}
