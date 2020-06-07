# MongoDB Password Policy

This repository is an attempt to enforce MongoDB password policies without resorting to LDAP.
Password policies generally cover the age of passwords and the complexity of passwords.

By capturing changes to the passwords, we are able to produce a history of password changes, as in the example below:

Look for the password history for the “melody” user in the “admin” database:

`MongoDB Enterprise > db.password_history.find({_id: "admin.melody"})`

Get the history of password changes and a hash representing the password:
```
{
  "_id" : "admin.melody",
  "history" : [ 
    { 
      "digested" : "5b2c67a0f6e99c9f5a39255db9c7deaa67f9826b56777fd8822589d4e1b8a867",
      "when" : ISODate("2020-06-06T20:05:40.183Z") 
    }, 
    { 
      "digested" : "0fae2dbf13bd2d5822da6b76a63bd987fd71154238407f0c097f9003abc2ca98",
      "when" : ISODate("2020-06-06T17:29:23.160Z") 
    }, 
    { 
      "digested" : "4699c87f1a63ecdf6c22ff054773d4fd239a8c6910606fb5d67ed129e51833d7",
      "when" : ISODate("2020-06-06T17:28:52.868Z") 
    }
  ] 
}
```
With this password history collection, we can produce a report of users who have not changed their passwords in the last ‘x’ days, and can additionally send out alerts or change the password to a random string upon password expiry.

Thoughts, comments, feedback? Create a GitHub issue!

## Setting Up

Schedule the password_change_capture.py script using cron or something similar. The history is stored in password_tracker.password_history.
