/*global __CONFIG__SECURITY_REGISTERABLE */
import React from 'react'
import { Link } from 'react-router'
import { make_url } from 'utils'
import { connect } from 'react-redux'
import { getExtensions } from 'config/extensions'
import {openLogin, openRegister} from 'actions/user_modal'
import mmStyles from 'components/MainMenu.scss'
import classnames from 'classnames'

const mapDispatchToProps = (state) => ({
  is_authenticated: !!state.CURRENT_USER,
  user: state.CURRENT_USER || {}
})

export class UserMenuWidget extends React.Component {
  static propTypes = {
    dispatch: React.PropTypes.func,
    is_authenticated: React.PropTypes.bool,
    user: React.PropTypes.object
  }

  renderLoggedOut () {
    if (__CONFIG__SECURITY_REGISTERABLE) {
      return <li className={mmStyles.navLink}>
                <button name="login_btn" onClick={(e) => this.props.dispatch(openLogin())}>
                  Login
                </button>
                <button name="signup_btn" onClick={(e) => this.props.dispatch(openRegister())}>
                  Sign up
                </button>
             </li>
    } else {
      return <li className={mmStyles.navLink}>
                <button name="login_btn" onClick={(e) => this.props.dispatch(openLogin())}>
                  Login
                </button>
              </li>
    }
  }

  render () {
    if (!this.props.is_authenticated) { return this.renderLoggedOut() }

    return <li name="usermenu" className={classnames(mmStyles.navLink, mmStyles.more)}>
              <Link to={make_url.users(this.props.user.id)}>Me</Link>
              <ul className={mmStyles.submenu}>
                {getExtensions('userNavigationItems').map(x => x.call(this))}
                <li><a name="logout" href='/logout'>Logout</a></li>
              </ul>
            </li>
  }
}

export default connect(mapDispatchToProps)(UserMenuWidget)
