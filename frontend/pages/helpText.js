import { Linking, Pressable, Text } from "react-native"

export default function HelpText(props) {

    return (

        <Text style={props.style}>
        {'\n'}
            Hello!{'\n'}
        {'\n'}
            I am the <Text style={{fontWeight:'bold'}}>help page!</Text>{'\n'}
        {'\n'}
            Not a lot is going on here right now... fill me with text later when you're ready.{'\n'}
        {'\n'}
            In the meantime... here's a
        {' '}
            
            <Pressable onPress={

                async () => {await Linking.openURL('https://youtu.be/B3jjFzRIMks?si=HQOZT2L6cjLlbuyo')
            }}>
                <Text style={[ props.style, {color: '#00f'}]}>
                    
                    funny video
                    
                </Text>
            </Pressable>

        </Text>
    )
}
