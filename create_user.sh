#!/bin/bash
HOST="http://user.ulake.usth.edu.vn/api/user"

username=$1
firstname=$2
lastname=$3
email=$4
password=$5

curl -v "$HOST" \
    -H "Content-Type: application/json" \
    -d '{
        "id": 0,
        "userName": "$username",
        "firstName": "$firstname",
        "lastName": "$lastname",
        "isAdmin": false,
        "email": "$email",
        "password": "$password",
        "registerTime": 0,
        "status": true,
        "code": "yourCode",
        "department": {
            "id": 0,
            "name": "yourDepartmentName",
            "address": "yourDepartmentAddress",
            "institution": {
                "id": 0,
                "name": "yourInstitutionName",
                "departments": [
                    "yourDepartmentName"
                ]
            },
            "users": [
                "yourUserName"
            ]
        },
        "groups": [
            {
                "id": 0,
                "name": "yourGroupName",
                "users": [
                    "yourUserName"
                ]
            }
        ]
    }'
