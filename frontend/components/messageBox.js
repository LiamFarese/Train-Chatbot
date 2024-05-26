
import { Text, View } from 'react-native';
import { useTheme } from '@react-navigation/native';
import styles from '../styles';


export default function MessageBox(props){
    
    const { colors } = useTheme()

    return (

        <View style={[

            styles(colors).container, 
            props.fill ? styles(colors).primary : {},
            {
                maxWidth: '80%',
                alignSelf: props.fill ? 'flex-start' : 'flex-end',
            }
        ]}>
            
            <Text style={[styles(colors).text, {

                color: props.fill ? 'white' : colors.text,
                textAlign: props.fill ? 'left' : 'right',
            }]}>
                {props.children}
            </Text>
        </View>
    )
}
