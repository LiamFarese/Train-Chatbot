import { Pressable, Text } from "react-native";
import styles from "../styles";
import { useTheme } from "@react-navigation/native";
import { useState } from "react";

export default function Button(props) {

    const colors = useTheme().colors;

    const [pressed, setPressed] = useState(false)

    return (

        <Pressable style={[
                
            styles(colors).container,
            props.primary ? styles(colors).primary : {},
        {
            backgroundColor: props.primary 
            ? (pressed ? colors.card : colors.primary)
            : (pressed ? colors.border : colors.card)
        }]}
            onPress={() => {

                setPressed(false)
                props.onPress()
            }}

            onPressIn={() => setPressed(true)}
            onPressOut={() => setPressed(false)}
        >
            <Text style={[
                
                styles(colors).text,
                props.primary ? {

                    color: 'white',
                } : {}
            ]}>
                {props.children}
                
            </Text>
        </Pressable>
    )
}
