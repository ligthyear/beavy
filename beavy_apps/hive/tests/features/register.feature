Feature: Registering at hive

    Background:
        Given a browser
        And I am logged out
        And I am a random new persona

    @wip
    Scenario: Register with a new account
        When I go to HOME
        When I press "signup_btn"
            Then I should see iframe "usermodal"
        When I switch to iframe "usermodal"
          Then I should see the form "register_user_form"

        When I fill in "email" with "$email"
          And I fill in "name" with "$name"
          And I fill in "password" with "password"
          And I click the submit button of form "register_user_form"
          And I click the link in the email I received at "$email"
        Then I should see an element with name "usermenu"
