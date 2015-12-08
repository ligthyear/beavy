import React, { PropTypes } from 'react'
import { MainMenu, styles as MainMenuStyles } from 'components/MainMenu'
import UserModal from 'containers/UserModal'
import UserMenuWidget from 'containers/UserMenuWidget'

import { make_url } from 'utils'
import { Link } from 'react-router'

import appStyles from './styles/hive_styles.scss'
import hiveMenustyles from './styles/hive_menu_styles.scss'
import { setupViews } from './setup'

setupViews()

// overwrite behaviour of the menu styles
Object.assign(MainMenuStyles, hiveMenustyles)

// insertExtension("MainNavigationTools", 0, () => <UserMenuWidget />)

export default class HiveApplication extends React.Component {
  static propTypes = {
    children: PropTypes.object
  }
  render () {
    return <div className={appStyles.hive}>
              <UserModal />
              <MainMenu
                styles={MainMenuStyles}
                logo='http://beavy.xyz/logos/logo.svg'
                navigationTools={<UserMenuWidget />}
              >

                <li>
                  <Link to={make_url.list('latest/')}>latest</Link>
                </li>
                <li>
                  <Link to='/submit/'>submit</Link>
                </li>

              </MainMenu>
              <div  className={appStyles.contentMain}>
                {this.props.children}
              </div>
            </div>
  }
}
