import { View, Text } from "react-native";
import MessageBox from "./messageBox";
import { useTheme } from '@react-navigation/native';

/*
    Message Block:
    
    props:
    - messages: list of messages
    - owner: string name of owner
    - left: align left and fill
*/

export default function MessageBlock(props) {

    const { colors } = useTheme();

    function GetMessageBoxes() {

        messageBoxes = []
        key = 0

        props.messages.forEach((message) => {
            
            messageBoxes.push(
                
                <View style={{marginTop: 2}} key={'margin' + key++}/>
            )
            
            messageBoxes.push(
                
                <MessageBox fill={props.left} key={'message' + key++}>{message}</MessageBox>
            )
        })

        return messageBoxes
    }

    return (

        <View style={{
            
            margin: 4,
        }}>
            <Text style={[styles(colors).text, {

                alignSelf: props.left ? 'flex-start' : 'flex-end',
                color: colors.text,
                marginLeft: 8,
                marginRight: 8,
            }]}>
                {props.owner}
                
            </Text>

            {GetMessageBoxes()}

        </View>
    )
}
