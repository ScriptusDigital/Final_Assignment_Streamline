import { useState } from 'react'
import {
    Link,
    Navigate,
    useLocation,
    useNavigate,
} from 'react-router'

import { ApiError } from '../api/client'
import { useAuth } from '../contexts/useAuth'
import '../styles/auth.css' 

    function getRegistrationErrorMessage(error) {   
        if (error instanceof ApiError) {
            const backendMessages =
                error.data?.non_field_errors

            if (
                Array.isArray(backendMessages) &&
                backendMessages.length > 0
            ) {
                return backendMessages[0]
            }

            return error.message
        }
        return 'Unable to register. Please try again'
    }           