from django.shortcuts import render, get_object_or_404
from .models import Listing

def listing_list(request):
    listings = Listing.published.all()
    
    return render(
        request, 
        'lost_and_found/listing/list.html', 
        {'listings': listings}
    )

def listing_detail(request, id):
    listing = get_object_or_404(
        Listing.published, 
        id=id
    )
    
    return render(
        request, 
        'lost_and_found/listing/detail.html', 
        {'listing': listing}
    )