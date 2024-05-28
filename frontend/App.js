import { useColorScheme } from 'react-native';
import {Appearance} from 'react-native';
import { DefaultTheme, DarkTheme, NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import colors from './colors'
import Chat from './pages/chat';
import { useState } from 'react';


const Stack = createNativeStackNavigator();

export default function App() {

  const scheme = useColorScheme();
  const [darkMode, setDarkMode] = useState(scheme === 'dark')

  return (

    <NavigationContainer theme={darkMode ? colors.darkColors : colors.lightColors}>

      <Stack.Navigator>
        
        <Stack.Screen 
          
          name="Chat"
          component={Chat}
          options={{headerShown: false }}
          initialParams={{ darkMode: darkMode, setDarkMode: setDarkMode }}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
