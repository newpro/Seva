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
            "type": "Transport",
            "rating": 4,
            "date_created": "2014-11-03",
            "price": "100 credits",
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
            "title": "Snow shoveling (small driveway)",
            "location": "63 Birch Street",
            "latitude": 51.544599,
            "longitude": -0.112588,
            "url": "item-detail.html",
            "type": "Household",
            "rating": 4,
            "date_created": "2014-11-03",
            "price": "200 credits",
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