import { useColorScheme } from 'react-native';
import { DefaultTheme, NavigationContainer } from '@react-navigation/native';
import { createNativeStackNavigator } from '@react-navigation/native-stack';
import { lightColors } from './colors'
import Chat from './pages/chat';


const Stack = createNativeStackNavigator();

export default function App() {

  const theme = lightColors;

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
