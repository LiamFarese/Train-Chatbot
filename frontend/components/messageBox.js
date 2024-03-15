
import { Text, View } from 'react-native';
import { useTheme } from '@react-navigation/native';


export default function MessageBox(props){
    
    const { colors } = useTheme();

    return (

        <View style={{
            
            maxWidth: '60%',
            backgroundColor: '#fff',
    
            borderColor: props.fill ? colors.primary : colors.border,
            borderRadius: 26,
            borderWidth: 2,
    
            backgroundColor: props.fill ? colors.primary : colors.card,
            alignSelf: props.fill ? 'flex-start' : 'flex-end',

            padding: 8,
            paddingLeft: 16,
            paddingRight: 16,
            margin: 4,
        }}>
            
            <Text style={{

                fontSize: 18,
                color: props.fill ? colors.card : colors.text,
                textAlign: props.fill ? 'left' : 'right',
            }}>
                {props.children}
            </Text>
        </View>
    )
}
