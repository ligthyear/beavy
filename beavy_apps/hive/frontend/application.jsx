
import React from "react";
import { MainMenu } from "components/MainMenu";
import UserModal from "containers/UserModal";
import UserMenuWidget from "containers/UserMenuWidget";

import { getExtensions } from "config/extensions";

// This is your app entry point
export default class Application extends React.Component {
    render() {
        return <div>
                  <UserModal />
                  <MainMenu
                    logo='http://beavy.xyz/logos/logo.svg'
                    navigationTools={<UserMenuWidget />}
                  >
                    {getExtensions('MainMenuItem').map(x=>x.call(this))}
                  </MainMenu>
                  {this.props.children}
                </div>;
    }
}

