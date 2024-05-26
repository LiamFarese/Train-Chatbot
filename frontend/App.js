import { useColorScheme } from 'react-native';
import {Appearance} from 'react-native';
import { DefaultTheme, DarkTheme, NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import colors from './colors'
import Chat from './pages/chat';


const Stack = createNativeStackNavigator();

export default function App() {

  const scheme = useColorScheme();
  const theme = scheme === 'dark' ? colors.darkColors : colors.lightColors;

  console.log(DarkTheme)

  return (

    <NavigationContainer theme={theme}>

      <Stack.Navigator>
        
        <Stack.Screen 
          
          name="Chat"
          component={Chat}
          options={{headerShown: false}}
        />
      </Stack.Navigator>
    </NavigationContainer>
  );
}
