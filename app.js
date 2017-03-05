var app = require('express')();
var cors = require('cors');

app.use(cors());
app.get('/',function(req,res){
    var resp = {
        data : [{
            "id": 1,
            "category": "Transport",
            "title": "Driver needed for doctor's appt",
            "location": "Toronto, Ontario",
            "latitude": 51.541599,
            "longitude": -0.112588,
            "url": "item-detail.html",
            "type": "Apartment",
            "type_icon": "assets/icons/store/apparel/umbrella-2.png",
            "rating": 4,
            "gallery":
                [
                ],
            "features":
                [
                ],
            "date_created": "2014-11-03",
            "price": "$2500",
            "featured": 0,
            "color": "",
            "person_id": 1,
            "year": 1980,
            "special_offer": 0,
            "item_specific":
                {
                },
            "description": "Curabitur odio nibh, luctus non ...",
            "last_review": "Curabitur odio nibh, luctus non ...",
            "last_review_rating": 5
        },
        {
            "id": 2,
            "category": "real_estate",
            "title": "Steak House Restaurant",
            "location": "63 Birch Street",
            "latitude": 51.544599,
            "longitude": -0.112588,
            "url": "item-detail.html",
            "type": "Apartment",
            "type_icon": "assets/icons/store/apparel/umbrella-2.png",
            "rating": 4,
            "gallery":
                [
                ],
            "features":
                [
                ],
            "date_created": "2014-11-03",
            "price": "$2500",
            "featured": 0,
            "color": "",
            "person_id": 1,
            "year": 1980,
            "special_offer": 0,
            "item_specific":
                {
                },
            "description": "Curabitur odio nibh, luctus non ...",
            "last_review": "Curabitur odio nibh, luctus non ...",
            "last_review_rating": 5
        }]
    };
    res.json(JSON.stringify(resp));
})
app.listen(8080);