from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate,login,logout
from prakhar_login import settings
from django.core.mail import send_mail,EmailMessage
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from django.utils.encoding import force_bytes,force_str
from . tokens import generate_token





# Create your views here.
def home(request):
    return render(request,"authentication/index.html")




#handle the signup request from the input
def signup(request):

    if request.method=="POST":
        #username = request.POST.get('username')
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']


        if User.objects.filter(username=username):
             messages.error(request,"Username already exists! Please try some other username")
             return redirect('signin')
        if User.objects.filter(email = email):
             messages.error(request,"Email already registered")
             return redirect('signin')
        
        if len(username) >10:
             messages.error(request,"Username must be under 10 characters")
        
        if pass1 !=pass2:
             messages.error(request,"Passwords didn't match!")

        if not username.isalnum():
             messages.error(request,"Username must be Alpha-Numeric")
             return redirect('signin')
        

    #django.contrib.auth.models is inbuilt python database
        myuser = User.objects.create_user(username,email,pass1)
        myuser.first_name = fname
        myuser.last_name = lname
        myuser.is_active = False
        myuser.save()

    # django.contrib is library for messages
    #this will print the message as the request completed successfully
        messages.success(request,"your account have been successully created.We have sent you a confirmation email, please confirm yoru email in order to activate your account")


    #Welcome email
        subject ="Welcome to Prakar's world"
        message ="hello" +myuser.first_name + "!! \n" + "Welcome to PRAKHAR's WORLD \n THANKS for visting our website \n we hve also sent you a confirmation email, please confirm your email address in order to activate your accoutn. \n\n thnaking you "
        from_email = settings.EMAIL_HOST_USER
        to_list= [myuser.email]
        send_mail(subject,message,from_email,to_list,fail_silently=True)

    #Email address confirmation 
        current_site = get_current_site(request)
        email_subject = "confirm your email @ PRAKHAR LOGIN !"
        message2 = render_to_string('email_confirmation.html',{
             'name':myuser.first_name,
             'domain':current_site.domain,
             'uid':urlsafe_base64_encode(force_bytes(myuser.pk)),
             'token':generate_token.make_token(myuser),
        })
        email = EmailMessage(
             email_subject,
             message2,
             settings.EMAIL_HOST_USER,
             [myuser.email],
        )
        email.fail_silently = True
        email.send()

    #redirect is the method in django.shortcuts 
    #this will redirect you the signin page after the above process is completed
        return redirect('community')
    
    return render(request,"authentication/signup.html")





def activate(request,uidb64,token):
    # User=get_user_model()
     try:
          uid = force_str(urlsafe_base64_decode(uidb64))
          myuser= User.objects.get(pk=uid)
    
     except():
         myuser = None

     if myuser is not None and generate_token.check_token(myuser,token):
         myuser.is_active = True
         myuser.save()
         login(request,myuser)
         messages.success(request,"your account has been activated")
         return redirect('signin')
     else:
          return render(request,'activation_failed.html')
     

#handles the signin request from the input
def signin(request):
        

        if request.method == 'POST':
             username = request.POST['username']
             pass1 = request.POST['pass1']

             user = authenticate(username =username,password =pass1)
             
             if user is not None:
                 login(request,user)
                 fname = user.first_name
                 return render(request,"authentication/index.html",{'fname':fname})
             else:
                 messages.error(request,"Bad Credentials!")
                 return redirect('home')
        
        return render(request,"authentication/signin.html")

        

def signout(request):
    logout(request)
    messages.success(request,"logged out successfully")
    return redirect('home') 



        