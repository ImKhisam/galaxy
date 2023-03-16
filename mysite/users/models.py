from django.db import models
from galaxy.models import CustomUser


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Teacher/', null=True, blank=True)
    status = models.BooleanField(default=False)


    #@property
    #def get_name(self):
    #    return self.user.first_name+" "+self.user.last_name

    #@property
    #def get_instance(self):
    #    return self

    def __str__(self):
        return self.user.first_name


class Student(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to='profile_pic/Student/', null=True, blank=True)



    #@property
    #def get_name(self):
    #    return self.user.first_name + " " + self.user.last_name

    #@property
    #def get_instance(self):
    #    return self
#
    def __str__(self):
        return self.user.first_name
