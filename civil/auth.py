def central_authorizations(user_obj, codename):
    """
    This function will be called *before* any other rule,
    so you can override all of the permissions here.
    """
    pass
    #isAuthorized = False
    #
    #if user_obj.get_profile().isUberAdmin():
    #    isAuthorized = True
    #elif user_obj.get_profile().isUserSupport() and codename in ['can_see_full_profile', 'can_delete_item']:
    #    isAuthorized = True
    #
    #return isAuthorized
