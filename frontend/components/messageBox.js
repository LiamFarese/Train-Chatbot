
import { Text, View, Linking } from 'react-native';
import { useTheme } from '@react-navigation/native';
import Hyperlink from 'react-native-hyperlink'
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
            <Hyperlink onPress={Linking.openURL}>

                <Text style={[styles(colors).text, {

                    color: props.fill ? 'white' : colors.text,
                    textAlign: props.fill ? 'left' : 'right',
                }]}>
                    {props.children}
                </Text>
            </Hyperlink>

        </View>
    )
}
