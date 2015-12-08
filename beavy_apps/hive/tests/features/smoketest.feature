Feature: Smoketesting the config

    Background:
        Given a browser

    Scenario: Smoketest for Home Page
        When I go to HOME
        Then I should see "Beavy Hive" within 5 seconds
        Then I should see "Login" within 5 seconds
